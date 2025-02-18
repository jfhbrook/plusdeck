#!/usr/bin/env perl

use v5.40;
use utf8;
use warnings;

use Data::Dumper;
use Getopt::Long;
use List::Util 'any';
use XML::Parser;

package main;

# TODO: Support other dbus-send flags:
# [--system | --session | --bus=ADDRESS | --peer=ADDRESS ]
# [--sender=NAME]
# [--reply-timeout=MSEC]

my $HELP = 'Usage: dbus-iface-markdown OPTIONS <PATH>

PARAMETERS:
  PATH  An optional path (defaults to /)

OPTIONS:
  --help         Show this help message
  --dest DEST    Dbus destination to document
  --out FILE     File to write output to (defaults to stdout)
  --system       Connect to the system bus
';

my $help = '';
my $dest;
my $file   = '';
my $out    = \*STDOUT;
my $system = '';

GetOptions(
    "help",   => \$help,
    "dest=s", => \$dest,
    "out=s"   => \$file,
    "system", => \$system
) or die($HELP);

my $path = "/";
if ( $#ARGV > 0 ) {
    $path = shift(@ARGV);
}

if ($help) {
    print $HELP;
    exit 0;
}

if ($file) {
    open( $out, '>', $file ) or die("Can not write to $file $!");
}

if ($system) {
    $system = '--system';
}

sub extract_response {
    my ($raw) = @_;
    $raw =~ s/\"$//;
    my @res = split /\n/, $raw;
    @res = splice @res, 3;
    join "\n", @res;
}

my $raw = `dbus-send --system \\
  --dest=$dest '$path' \\
  --print-reply \\
  org.freedesktop.DBus.Introspectable.Introspect`;

my $res = &extract_response($raw);

my $parser = XML::Parser->new( Style => 'Tree' );
my $bus    = $parser->parse($res);

&process_bus( @{ $bus->[1] } );

close $out;

sub process_bus {
    print $out "# $dest ($path)\n\n";
    while (@_) {
        my $child = shift;
        if ( $child eq 'interface' ) {
            my $iface = shift;
            &process_iface( @{$iface} );
        }
    }
}

sub process_iface {
    my %props = %{ shift @_ };

    if ( $props{'name'} =~ /^org.freedesktop/ ) {
        return;
    }
    print $out "## Interface: $props{'name'}\n\n";
    while (@_) {
        my $child = shift;
        if ( $child eq 0 ) {
            shift;
            next;
        }
        elsif ( $child eq 'method' ) {
            &process_method( @{ shift @_ } );
        }
        elsif ( $child eq 'property' ) {
            &process_property( @{ shift @_ } );
        }
        elsif ( $child eq 'signal' ) {
            &process_signal( @{ shift @_ } );
        }
        else {
            print $out Dumper($child);
        }
    }
}

sub process_method {
    my %props = %{ shift @_ };
    print $out "### Method: $props{'name'}\n\n";
    my @args;
    my $ret = 'void';
    my @anns;

    while (@_) {
        my $child = shift;
        if ( $child eq 0 ) {
            shift;
            next;
        }
        elsif ( $child eq 'arg' ) {
            my @children = @{ shift @_ };
            my %props    = %{ $children[0] };
            if ( $props{'direction'} eq 'in' ) {
                push( @args, $props{'type'} );
            }
            elsif ( $props{'direction'} eq 'out' ) {
                $ret = $props{'type'};
            }
            else {
                print $out Dumper(%props);
            }
        }
        elsif ( $child eq 'annotation' ) {
            my $ann = &process_annotation( @{ shift @_ } );
            push @anns, $ann;
        }
        else {
            print $out Dumper($child);
        }
    }

    if (@args) {
        print $out '**Arguments:** ';
        print $out join( ", ", map { "`$_`" } @args ) . "\n";
        print $out "\n";
    }
    print $out "**Returns:** `$ret`\n\n";

    print_annotations(@anns);
}

sub process_property {
    my %props = %{ shift @_ };
    print $out "### Property: $props{'name'}\n\n";
    my $type   = $props{'type'};
    my $access = $props{'access'};
    my @anns;

    print $out "**Type:** `$type`\n\n";
    print $out "**Access:** `$access`\n";

    while (@_) {
        my $child = shift;
        if ( $child eq 0 ) {
            shift;
            next;
        }
        elsif ( $child eq 'annotation' ) {
            my $ann = &process_annotation( @{ shift @_ } );
            push @anns, $ann;
        }
        else {
            print $out Dumper($child);
        }
    }

    if (@anns) {
        print $out "\n";
    }

    print_annotations(@anns);
}

sub process_signal {
    my %props = %{ shift @_ };
    print $out "### Signal: $props{'name'}\n\n";
    my $type = 'void';
    my @anns;

    while (@_) {
        my $child = shift;
        if ( $child eq 0 ) {
            shift;
            next;
        }
        elsif ( $child eq 'arg' ) {
            my @children = @{ shift @_ };
            my %props    = %{ $children[0] };
            $type = $props{'type'};
        }
        elsif ( $child eq 'annotation' ) {
            my $ann = &process_annotation( @{ shift @_ } );
            push @anns, $ann;
        }
        else {
            print $out Dumper($child);
        }
    }

    print $out "**Type**: `$type`\n\n";
    print_annotations(@anns);
}

sub process_annotation {
    my %props = %{ shift @_ };
    "- $props{'name'}: `$props{'value'}`";
}

sub print_annotations {
    if ( !@_ ) {
        return;
    }

    print $out "**Annotations:**\n\n";
    foreach (@_) {
        print $out "$_\n";
    }
    print $out "\n";
}
