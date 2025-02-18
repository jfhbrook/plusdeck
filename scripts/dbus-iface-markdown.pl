#!/usr/bin/env perl

use v5.40;
use utf8;
use warnings;

use Data::Dumper;
use XML::Parser;

package main;

sub extract_response {
    my ($raw) = @_;
    $raw =~ s/\"$//;
    my @res = split /\n/, $raw;
    @res = splice @res, 3;
    join "\n", @res;
}

my $cmd = 'dbus-send --system \
  --dest=org.jfhbrook.plusdeck "/" \
  --print-reply \
  org.freedesktop.DBus.Introspectable.Introspect';

my $raw = `$cmd`;
my $res = &extract_response($raw);

my $parser = XML::Parser->new( Style => 'Tree' );
my $bus    = $parser->parse($res);

my $iface_name = 'org.jfhbrook.plusdeck';

&process_bus( @{ $bus->[1] } );

sub process_bus {
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

    if ( $props{'name'} eq $iface_name ) {
        print "## $props{'name'}\n\n";
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
                print Dumper($child);
            }
        }
    }
}

sub process_method {
    my %props = %{ shift @_ };
    print "### Method: $props{'name'}\n\n";
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
                print "Unexpected arg props:\n";
                print Dumper(%props);
            }
        }
        elsif ( $child eq 'annotation' ) {
            my $ann = &process_annotation( @{ shift @_ } );
            push @anns, $ann;
        }
        else {
            print Dumper($child);
        }
    }

    print_annotations(@anns);

    if (@args) {
        print '**Arguments:** ';
        print join( ", ", @args ) . "\n";
    }
    print "**Returns: $ret\n\n";
}

sub process_property {
    my %props = %{ shift @_ };
    print "### Property: $props{'name'}\n\n";
    my @anns;

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
            print Dumper($child);
        }
    }

    print_annotations(@anns);
}

sub process_signal {
    my %props = %{ shift @_ };
    print "### Signal: $props{'name'}\n\n";
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
            print Dumper($child);
        }
    }

    print_annotations(@anns);
    print "**Type: $type\n\n";
}

sub process_annotation {
    my %props = %{ shift @_ };
    "- $props{'name'}: $props{'value'}";
}

sub print_annotations {
    if ( !@_ ) {
        return;
    }

    print "**Annotations:**\n\n";
    foreach (@_) {
        print "$_\n";
    }
    print "\n";
}
